<%inherit file="/base_unauthenticated.mako" />
<% from logcabin.models import User %>
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
    <p><a href="${request.route_path("account.forgot_password")}">Forgotten your password?</a></p>
    <p class="controls"><button type="submit">Log in</button></p>
  </form>

