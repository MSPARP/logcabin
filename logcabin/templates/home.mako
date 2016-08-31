<%inherit file="/base.mako" />
<%block name="title">Welcome to </%block>
<h1>Log Cabin</h1>
<div id="content">
  <p>Welcome to Log Cabin. <a href="${request.route_path("logs.new")}">Write a new log</a> or <a href="${request.route_path("fandoms.categories")}">browse existing ones</a>.</p>
</div>
