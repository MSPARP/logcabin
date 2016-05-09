<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s favorites - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("users.profile", username=request.context.username)}">${request.context.username}</a></li>
  </ul>
</nav>

<h1>${request.context.username}'s favorites</h1>

<ul>
  % for favorite in favorites:
  <li>
    <a href="${request.route_path("logs.log", log_id=favorite.log.id)}">${favorite.log.name}</a>
    % if favorite.log.summary:
    <p>${favorite.log.summary}</p>
    % endif
  </li>
  % endfor
</ul>

