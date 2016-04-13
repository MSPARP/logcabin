<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s cabin - </%block>

<h1>${request.context.username}'s cabin</h1>

<h2>Recent logs</h2>
<ul>
  % for log in recent_logs:
  <li><a href="${request.route_path("logs.log", id=log.id)}">${log.name}</a></li>
  % endfor
</ul>

<h2>Favorites</h2>
<ul>
  % for favorite in favorites:
  <li><a href="${request.route_path("logs.log", id=favorite.log.id)}">${favorite.log.name}</a></li>
  % endfor
</ul>

<h2>Subscribed to</h2>
<ul>
  % for subscription in log_subscriptions:
  <li><a href="${request.route_path("logs.log", id=subscription.log.id)}">${subscription.log.name}</a></li>
  % endfor
</ul>

