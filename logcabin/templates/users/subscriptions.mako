<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s subscriptions - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("users.profile", username=request.context.username)}">${request.context.username}</a></li>
  </ul>
</nav>

<h1>${request.context.username}'s subscriptions</h1>

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

