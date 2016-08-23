from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

from logcabin.models import FandomCategory, Fandom


@view_config(route_name="fandoms.categories", permission=NO_PERMISSION_REQUIRED, renderer="fandoms/categories.mako")
def fandom_categories(request):
    return {"categories": request.db.query(FandomCategory).order_by(FandomCategory.name).all()}


@view_config(route_name="fandoms.category", permission=NO_PERMISSION_REQUIRED, renderer="fandoms/category.mako")
def fandom_category(context, request):
    return {"fandoms": request.db.query(Fandom).filter(Fandom.category_id == context.id).order_by(Fandom.name).all()}
