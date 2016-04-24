<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s cabin - </%block>

<h1>${request.context.username}'s cabin</h1>

<h2>Recent logs</h2>
<ul>
  % for log in recent_logs:
  <li>
    <a href="${request.route_path("logs.log", log_id=log.id)}">${log.name}</a>
    % if log.summary:
    <p>${log.summary}</p>
    % endif
  </li>
  % endfor
</ul>
<p><a href="${request.route_path("users.logs", username=request.context.username)}">More</a></p>

<h2>Favorites</h2>
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
<p><a href="${request.route_path("users.favorites", username=request.context.username)}">More</a></p>

<h2>Subscribed to</h2>
<ul>
  % for subscription in log_subscriptions:
  <li>
    <a href="${request.route_path("logs.log", log_id=subscription.log.id)}">${subscription.log.name}</a>
    % if subscription.log.summary:
    <p>${subscription.log.summary}</p>
    % endif
  </li>
  % endfor
</ul>
<p><a href="${request.route_path("users.subscriptions", username=request.context.username)}">More</a></p>

