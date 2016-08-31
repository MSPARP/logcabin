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

<header>
  <div id="header_inner">
    <a id="logo" href="${request.route_path("home")}">Log Cabin</a>
    % if request.user:
    <nav>
      <ul>
        <li><a href="${request.route_path("users.profile", username=request.user.username)}">Your cabin</a></li>
        <li><a href="${request.route_path("upload")}">Upload</a></li>
        <li><a href="${request.route_path("fandoms.categories")}">Browse</a></li>
        <li><a href="${request.route_path("account.settings")}">Settings</a></li>
        <li>
          <form action="${request.route_path("account.log_out")}" method="post">
            <button type="submit">Log out</button>
          </form>
        </li>
      </ul>
    </nav>
    % endif
  </div>
</header>

<% flash_messages = request.session.pop_flash() %>
% if flash_messages:
<ul id="flash_messages">
  % for message in flash_messages:
  <li>${message}</li>
  % endfor
</ul>
% endif

<main>
${next.body()}
</main>

<footer></footer>

<script src="/static/logcabin.js"></script>

</body>
</html>
