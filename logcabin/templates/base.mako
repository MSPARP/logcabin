<!DOCTYPE html>
<html>
<head>
<title><%block name="title"></%block>Log Cabin</title>
<link rel="stylesheet" href="/static/normalize.css">
<link rel="stylesheet" href="/static/logcabin.css">
% for content_type, url in request.extensions:
<link rel="alternate" type="${content_type}" href="${url}">
% endfor
</head>
<body class="<%block name="body_class"></%block>">

<% flash_messages = request.session.pop_flash() %>
% if flash_messages:
<ul class="flash_messages">
  % for message in flash_messages:
  <li>${message}</li>
  % endfor
</ul>
% endif

${next.body()}

<script src="/static/logcabin.js"></script>

</body>
</html>
