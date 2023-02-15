import aieco.models as model

def GlobalContext(request):
    
    """
    Generates a global context with basic user information for use by all views of the project.
    "aieco/core/settings.py"
    TEMPLATES = [{'OPTIONS': {'context_processors': ['aieco.functions.GlobalContext',],},},]
    """
    
    if request.user.id is not None:
        rUser = request.user

        InfoUser = model.Account.objects.get(id=rUser.id)

        return {
            'InfoUser':InfoUser,                                    
            }
        
    return {}   