<%inherit file="/base.mako" />
<%block name="title">${request.context.log.name}, ${request.context.name} - </%block>

<h1>${request.context.log.name}, ${request.context.name}</h1>

% for message in messages:
<div id="message${message.id}">${message.text}</div>
% endfor

