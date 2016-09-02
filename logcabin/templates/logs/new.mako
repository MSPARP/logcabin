<%inherit file="/base.mako" />
<% from logcabin.models import Log %>
<%block name="title">New log - </%block>
<h1>New log</h1>
<div id="content" class="log_body">
  <form action="${request.route_path("logs.new")}" method="post">
    <p>Name: <input type="text" name="name" required maxlength="${Log.name.type.length}" value="${request.POST.get("name", "")}"></p>
    % if error == "name":
    <p class="error">Please enter a name.</p>
    % endif
    <p>Rating: <select name="rating">
      % for rating, name in Log.ratings.items():
      <option value="${rating}">${name}</option>
      % endfor
    </select></p>
    % if error == "rating":
    <p class="error">Please select a rating.</p>
    % endif
    <p>Summary: <textarea name="summary">${request.POST.get("summary", "")}</textarea></p>
    <p><label><input type="checkbox" name="posted_anonymously"> Post anonymously</label></p>
    <section>
      <textarea name="message">${request.POST.get("message", "")}</textarea>
      % if error == "message":
      <p class="error">Please write some text.</p>
      % endif
      <button type="submit">Save</button>
    </section>
  </form>
</div>
