<%inherit file="/base.mako" />
<%block name="title">${request.context.username}'s logs - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("users.profile", username=request.context.username)}">${request.context.username}</a></li>
  </ul>
</nav>
<h1>${request.context.username}'s logs</h1>
<div id="content">
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
</div>
