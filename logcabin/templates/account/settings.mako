<%inherit file="/base.mako" />
<% from logcabin.models import User %>
<%block name="title">Settings - </%block>
<h1>Settings</h1>
<div id="content">
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
  <section>
    <h2>Linked accounts</h2>
    % if cherubplay_accounts:
    <h3>Cherubplay</h3>
    <ul>
      % for account in cherubplay_accounts:
      <li>${account["username"]}</li>
      % endfor
    </ul>
    % endif
    % if msparp_accounts:
    <h3>MSPARP</h3>
    <ul>
      % for account in msparp_accounts:
      <li>${account["username"]}</li>
      % endfor
    </ul>
    % endif
    <h3>Tumblr</h3>
    <form action="${request.route_path("account.tumblr")}" method="post">
      <p><button>Connect a Tumblr account</button></p>
    </form>
    % if request.user.tumblr_accounts:
    <ul>
      % for account, user_info in tumblr_accounts:
      <li><a href="https://${user_info["name"]}.tumblr.com/">${user_info["name"]}</a></li>
      % endfor
    </ul>
    % endif
  </section>
</div>
