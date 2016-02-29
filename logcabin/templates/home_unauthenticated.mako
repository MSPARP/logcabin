<%inherit file="base.mako" />
<%block name="title">Welcome to </%block>
<%block name="body_class">unauthenticated</%block>
<% from logcabin.models import User %>

<h1>Log Cabin</h1>

<% flash_messages = request.session.pop_flash() %>
% if flash_messages:
<ul class="flash_messages">
  % for message in flash_messages:
  <li>${message}</li>
  % endfor
</ul>
% endif

<section id="account_forms">
  <form action="${request.route_path("account.register")}" method="post" class="ajax_form">
    <h3>Register</h3>
    <p class="error"></p>
    <p><input type="text" name="username" maxlength="${User.username.type.length}" required placeholder="Username..."></p>
    <p><input type="email" name="email_address" maxlength="${User.email_address.type.length}" required placeholder="Email address..."></p>
    <p><input type="password" name="password" required placeholder="Password..."></p>
    <p><input type="password" name="password_again" required placeholder="Password again..."></p>
    <p class="controls"><button type="submit">Register</button></p>
  </form>
  <form action="${request.route_path("account.log_in")}" method="post" class="ajax_form">
    <h3>Log in</h3>
    <p class="error"></p>
    <p><input type="text" name="username" maxlength="${User.username.type.length}" required placeholder="Username..."></p>
    <p><input type="password" name="password" required placeholder="Password..."></p>
    <p class="controls"><button type="submit">Log in</button></p>
  </form>
</section>
