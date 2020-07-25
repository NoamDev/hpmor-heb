import os
import collections
from os.path import join, basename, dirname, splitext, relpath, isfile
import importlib
import datetime
import glob
import requests
import backoff

data = 'data'
dist = 'dist'

modified = {}


def load(name):
    ids_dir = join(data, name, 'ids')

    ids_dict = {f: open(join(ids_dir, f)).read()
                for f in os.listdir(ids_dir)}
    ids_dict = collections.OrderedDict(ids_dict)
    modified_times = get_modified_times(ids_dict)

    packers_dict = {}

    strcture_scripts = join('structure', name, '**/*.py')
    for script in glob.glob(strcture_scripts, recursive=True):
        script_name, _ = splitext(script)
        module = importlib.import_module(script_name.replace(os.sep, '.'))
        dist_path = join(dist, relpath(script_name, 'structure'))
        packers_dict[dist_path] = module.pack

    requirements = collections.defaultdict(set)
    for dist_path, packers in packers_dict.items():
        for packer in packers:
            packer_requ = packer.requirements(ids_dict)
            for downloader_cls, ids in packer_requ:
                requirements[downloader_cls].update(ids)

    # Add indirect requirements
    extended_requirements = requirements.copy()
    for downloader_cls, ids in requirements.items():
        required = downloader_cls.requires()
        while required:
            cls = required.pop()
            extended_requirements[cls].update(ids)
            required.extend(cls.requires())
    requirements = extended_requirements

    downloaders = {cls: cls(dist) for cls in requirements.keys()}
    for cls, ids in requirements.items():
        d = downloaders[cls]
        requirements[cls].update(ids)

    modified = {cls: get_modified_ids(d, modified_times)
                for cls, d in downloaders.items()}

    # sort downloaders by dependency
    ordered_downloaders = collections.OrderedDict()
    dependencies_list = [(cls, cls.requires()) for cls in downloaders.keys()]
    sorted_dependencies = topological_sort(dependencies_list)

    for cls in sorted_dependencies:
        ordered_downloaders[cls] = downloaders[cls]

    for cls, d in ordered_downloaders.items():
        ids_to_download = list(modified[cls])
        d.download(ids_to_download)
        for id in ids_to_download:
            d.set_modified(id, modified_times[id])
    print("Packing...")
    for dist_path, packers in packers_dict.items():
        for packer in packers:
            # if not requirements have changed since last build we can skip
            if should_skip(packer, modified, ids_dict, dist_path):
                continue
            os.makedirs(dist_path, exist_ok=True)
            packer.pack(dist_path, ids_dict)


def should_skip(packer, modified, ids_dict, dist_path):
    return not any(set(modified[cls]).intersection(ids)
                   for cls, ids in packer.requirements(ids_dict)) \
               and isfile(packer.get_dst(dist_path))


def get_modified_ids(d, modified_times):
    return [id for id, modified_time in modified_times.items()
            if d.get_modified(id) != modified_time]


def get_modified_times(ids_dict):
    print("Getting last modified times...")
    session = requests.session()
    ids = list(ids_dict.values())
    res = {id: get_last_modified(id, session) for id in ids}
    print("Done.")
    return res


class ForbiddenError(Exception):
    pass


@backoff.on_exception(backoff.expo, ForbiddenError, max_time=60)
def get_last_modified(gid, session):
    template_url = 'https://www.googleapis.com/drive/v3/files/{id}' \
                    + '?fields=modifiedTime&key={key}'
    url = template_url.format(id=gid, key=os.environ['DRIVE_API_KEY'])
    r = session.get(url)
    if r.status_code == 403:
        print("get_last_modified: too many requests. maybe retrying..")
        raise ForbiddenError("Could not contact drive api. status: 403")
    body = r.json()
    return body['modifiedTime']


def topological_sort(source):
    """perform topo sort on elements.

    :arg source: list of ``(name, [list of dependancies])`` pairs
    :returns: list of names, with dependancies listed first
    """
    # copy deps so we can modify set in-place
    pending = [(name, set(deps)) for name, deps in source]
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, deps = entry
            deps.difference_update(emitted)  # remove deps we emitted last pass
            if deps:  # still has deps? recheck during next pass
                next_pending.append(entry)
            else:  # no more deps? time to emit
                yield name
                # The following is not required,
                # but helps preserve original ordering.
                emitted.append(name)
                # remember what we emitted for difference_update() in next pass
                next_emitted.append(name)
        if not next_emitted:
            # all entries have unmet deps, one of two things is wrong...
            raise ValueError("cyclic or missing dependancy detected: %r"
                             % (next_pending,))
        pending = next_pending
        emitted = next_emitted
