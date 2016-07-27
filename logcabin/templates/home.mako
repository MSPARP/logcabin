<%inherit file="/base.mako" />
<%block name="title">Welcome to </%block>
<h1>Log Cabin</h1>
<div id="content">
  <section>
    <form action="${request.route_path("account.log_out")}" method="post">
      <p>Logged in as ${request.user.username}.</p>
      <p><button type="submit">Log out</button></p>
    </form>
  </section>
</div>
