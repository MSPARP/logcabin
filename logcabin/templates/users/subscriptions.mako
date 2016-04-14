<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s subscriptions - </%block>

<h1>${request.context.username}'s subscriptions</h1>

<ul>
  % for subscription in log_subscriptions:
  <li><a href="${request.route_path("logs.log", id=subscription.log.id)}">${subscription.log.name}</a></li>
  % endfor
</ul>

