<%inherit file="/base.mako" />
<%block name="title">${request.context.name} - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("fandoms.categories")}">Fandoms</a></li>
    <li><a href="${request.route_path("fandoms.category", category_url_name=request.context.category.url_name)}">${request.context.category.name}</a></li>
  </ul>
</nav>
<h1>${request.context.name}</h1>
<div id="content">
  <ul>
    % for log in logs:
    <li><a href="${request.route_path("logs.log", log_id=log.id)}">${log.name}</a></li>
    % endfor
  </ul>
</div>
