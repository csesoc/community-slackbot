import os

TEST_VIEW_ONE = "test"
__CACHED_VIEWS = {}


def try_load_view(view):
    """
    Attempts to load block kit view directly from file
    :param view:
    :return:
    """
    view_path = os.path.join("/views", view)
    if os.path.exists(view_path):
        return open(view_path, "r").read()
    return None


def get_block_view(view):
    """
    Gets a block kit view from the given identifier name
    :param view: Block kit view identifier name
    :return: JSON String representation of block view
    """
    if view in __CACHED_VIEWS:
        return __CACHED_VIEWS[view]

    loaded_view = try_load_view(view)
    if loaded_view is not None:
        __CACHED_VIEWS[view] = loaded_view
    return loaded_view
