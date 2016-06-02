<%inherit file="/base_unauthenticated.mako" />
<% from logcabin.models import User %>
  <form action="${request.route_path("account.forgot_password")}" method="post">
    <h3>Reset your password</h3>
    <p class="error"></p>
    <p><input type="text" name="username" maxlength="${User.username.type.length}" required placeholder="Username..."></p>
    <p class="controls"><button type="submit">Request a reset</button></p>
  </form>

