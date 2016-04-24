<%inherit file="/base.mako" />
<%block name="title">${request.context.name} - </%block>

<h1>${request.context.name}</h1>

<p>by <a href="${request.route_path("users.profile", username=request.context.creator.username)}">${request.context.creator.username}</a></p>

<p>Summary: ${request.context.summary}</p>

<p><a href="${request.route_path("logs.chapters", log_id=request.context.id)}">Chapters</a></p>
