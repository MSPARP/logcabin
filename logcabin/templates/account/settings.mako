<%inherit file="/base.mako" />
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
