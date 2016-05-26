<%inherit file="/base.mako" />
<% from logcabin.models import User %>
<%block name="title">Settings - </%block>

<h1>Settings</h1>

<section>
  <h2>Change your password</h2>
  <form action="${request.route_path("account.change_password")}" method="post">
    <p><input type="password" name="old_password" required placeholder="Old password..."></p>
    <p><input type="password" name="new_password" required placeholder="New password..."></p>
    <p><input type="password" name="new_password_again" required placeholder="New password again..."></p>
    <p><button type="submit">Change</button></p>
  </form>
</section>

<section>
  <h2>Change your email address</h2>
  <form action="${request.route_path("account.change_email")}" method="post" class="ajax_form">
    <p class="error"></p>
    <p><input type="email" name="email_address" maxlength="${User.email_address.type.length}" required placeholder="Email address..."></p>
    <p class="controls"><button type="submit">Change</button></p>
  </form>
</section>
