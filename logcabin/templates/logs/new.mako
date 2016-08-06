<%inherit file="/base.mako" />
<%block name="title">New log - </%block>
<h1>New log</h1>
<div id="content" class="log_body">
  <form action="${request.route_path("logs.new")}" method="post">
    <section>
      <textarea name="message"></textarea>
      <button type="submit">Save</button>
    </section>
  </form>
</div>
