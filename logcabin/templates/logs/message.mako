<%inherit file="/base.mako" />
<%block name="title">Edit message - </%block>
<nav id="breadcrumb">
  <ul>
    <li><a href="${request.route_path("logs.log", log_id=request.context.log.id)}">${request.context.log.name}</a></li>
    <li><a href="${request.route_path("logs.chapters", log_id=request.context.log.id)}">Chapters</a></li>
    <li><a href="${request.route_path("logs.chapter", log_id=request.context.log.id, number=request.context.number)}">${request.context.name}</a></li>
  </ul>
</nav>
<h1>Edit message</h1>
<div id="content">
  <form action="${request.route_path("logs.chapter", log_id=request.context.log_id, number=request.context.number)}" method="post">
    <p><textarea name="edit_${message_revision.message.id}">${message_revision.text}</textarea></p>
    <p><button type="submit">Save</button></p>
  </form>
</div>
