<%inherit file="base.mako" />
<%block name="title">Welcome to </%block>

<h1>Log Cabin</h1>

<% flash_messages = request.session.pop_flash() %>
% if flash_messages:
<ul class="flash_messages">
  % for message in flash_messages:
  <li>${message}</li>
  % endfor
</ul>
% endif

<section>
  <form action="${request.route_path("account.log_out")}" method="post">
    <p>Logged in as ${request.user.username}.</p>
    <p><button type="submit">Log out</button></p>
  </form>
</section>
