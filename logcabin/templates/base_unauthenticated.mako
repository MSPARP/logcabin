<!DOCTYPE html>
<% from logcabin.models import User %>
<html>
<head>
<title>Welcome to Log Cabin</title>
<link rel="stylesheet" href="/static/normalize.css">
<link rel="stylesheet" href="/static/logcabin.css">
</head>
<body class="unauthenticated">

<h1>Log Cabin</h1>

<% flash_messages = request.session.pop_flash() %>
% if flash_messages:
<ul id="flash_messages">
  % for message in flash_messages:
  <li>${message}</li>
  % endfor
</ul>
% endif

<section id="account_forms">
% if hasattr(next, "body"):
${next.body()}
% endif
</section>

<script src="/static/logcabin.js"></script>

</body>
</html>
