import aieco.models as model

def GlobalContext(request):
    
    """
    Generates a global context with basic user information for use by all views of the project.
    "aieco/core/settings.py"
    TEMPLATES = [{'OPTIONS': {'context_processors': ['aieco.functions.GlobalContext',],},},]
    """
    
    if request.user.id is not None:
        Setting = model.Settings.objects.filter(IsActive=True).first()
        Info = model.Information.objects.filter(IsActive=True).order_by("id")

        return {
            'Setting':Setting,
            "Info":Info,
            }
        
    return {}  