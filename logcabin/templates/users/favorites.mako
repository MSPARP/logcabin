<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s favorites - </%block>

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

