1. Resolve the error by adding the following code 
2. Debugging and fixing dependency issues , dependency conflict , dependency of version , deprivated version 


*Traceback (most recent call last):
  File "C:\Users\DELL\Downloads\IEEE Techsangam\mvp\agent\venv\Lib\site-packages\gradio\queueing.py", line 626, in process_events
    response = await route_utils.call_process_api(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<5 lines>...
    )
    ^
  File "C:\Users\DELL\Downloads\IEEE Techsangam\mvp\agent\venv\Lib\site-packages\gradio\route_utils.py", line 350, in call_process_api
    output = await app.get_blocks().process_api(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<11 lines>...
    )
    ^
  File "C:\Users\DELL\Downloads\IEEE Techsangam\mvp\agent\venv\Lib\site-packages\gradio\blocks.py", line 2260, in process_api
    data = await self.postprocess_data(block_fn, result["prediction"], state)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\Downloads\IEEE Techsangam\mvp\agent\venv\Lib\site-packages\gradio\blocks.py", line 2038, in postprocess_data
    prediction_value = block.postprocess(prediction_value)
  File "C:\Users\DELL\Downloads\IEEE Techsangam\mvp\agent\venv\Lib\site-packages\gradio\components\chatbot.py", line 635, in postprocess
    self._check_format(value, "messages")
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "C:\Users\DELL\Downloads\IEEE Techsangam\mvp\agent\venv\Lib\site-packages\gradio\components\chatbot.py", line 423, in _check_format
    raise Error(
        "Data incompatible with messages format. Each message should be a dictionary with 'role' and 'content' keys or a ChatMessage object."
    )
gradio.exceptions.Error: "Data incompatible with messages format. Each message should be a dictionary with 'role' and 'content' keys or a ChatMessage object."
