<%inherit file="/base.mako" />
<%block name="title">${request.context.name} - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("fandoms.categories")}">Fandoms</a></li>
  </ul>
</nav>
<h1>${request.context.name}</h1>
<div id="content">
  % if fandoms:
  <ul>
    % for fandom in fandoms:
    <li><a href="${request.route_path("fandoms.fandom", category_url_name=request.context.url_name, fandom_url_name=fandom.url_name)}">${fandom.name}</a></li>
    % endfor
  </ul>
  % else:
  <p>There are no fandoms under ${request.context.name}.</p>
  % endif
</div>
