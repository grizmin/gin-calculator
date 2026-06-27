from gin_calculator import __version__

def app_version(request):
    return {'app_version': __version__}
