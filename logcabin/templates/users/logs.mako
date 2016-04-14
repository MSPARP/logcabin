<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s logs - </%block>

<h1>${request.context.username}'s logs</h1>

<ul>
  % for log in recent_logs:
  <li><a href="${request.route_path("logs.log", id=log.id)}">${log.name}</a></li>
  % endfor
</ul>

