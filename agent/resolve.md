disclaimer and note:
1.Make sure to analyse the affected folder thouroughly.
2.we are working on making an agent companion and agent clinician assistant for my mentaid project which you will find in the diretory.
3.make sure not to execute any commands without my permission.
4.analyse the issues and then tell me exactly whats causing it using online docs and my repo itself.
5.provide 3 top solutions for each issue.
6.I am a beginner so please be patient with me.
7.After identifying the issues present the exact implementation plan you are going to use to resolve the issue.
8.Proceed only when i allow you unless dont.

issue to resolve:
analyse this:(venv) PS C:\Users\DELL\Downloads\IEEE Techsangam\demo dashboard\patient-dashboard\agent> pip install -r "requirements.txt"
Collecting fastapi<0.116.0,>=0.115.0 (from -r requirements.txt (line 2))
  Downloading fastapi-0.115.14-py3-none-any.whl.metadata (27 kB)
Collecting uvicorn<0.36.0,>=0.35.0 (from uvicorn[standard]<0.36.0,>=0.35.0->-r requirements.txt (line 3))
  Using cached uvicorn-0.35.0-py3-none-any.whl.metadata (6.5 kB)
Collecting pydantic<2.12.0,>=2.11.0 (from -r requirements.txt (line 4))
  Using cached pydantic-2.11.7-py3-none-any.whl.metadata (67 kB)
Collecting pandas<2.4.0,>=2.3.0 (from -r requirements.txt (line 7))
  Using cached pandas-2.3.1-cp313-cp313-win_amd64.whl.metadata (19 kB)
Collecting numpy<2.4.0,>=1.26.0 (from -r requirements.txt (line 8))
  Using cached numpy-2.3.2-cp313-cp313-win_amd64.whl.metadata (60 kB)
Collecting python-dotenv<1.2.0,>=1.1.0 (from -r requirements.txt (line 11))
  Using cached python_dotenv-1.1.1-py3-none-any.whl.metadata (24 kB)
Collecting requests<2.33.0,>=2.32.0 (from -r requirements.txt (line 14))
  Using cached requests-2.32.4-py3-none-any.whl.metadata (4.9 kB)
Collecting urllib3<3.0.0,>=2.5.0 (from -r requirements.txt (line 15))
  Using cached urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
Collecting certifi>=2025.8.0 (from -r requirements.txt (line 16))
  Using cached certifi-2025.8.3-py3-none-any.whl.metadata (2.4 kB)
Collecting gradio<5.43.0,>=5.42.0 (from -r requirements.txt (line 19))
  Using cached gradio-5.42.0-py3-none-any.whl.metadata (16 kB)
Collecting typing-extensions<4.15.0,>=4.14.0 (from -r requirements.txt (line 22))
  Using cached typing_extensions-4.14.1-py3-none-any.whl.metadata (3.0 kB)
Collecting python-multipart<0.1.0,>=0.0.20 (from -r requirements.txt (line 25))
  Using cached python_multipart-0.0.20-py3-none-any.whl.metadata (1.8 kB)
Collecting email-validator<3.0.0,>=2.0.0 (from -r requirements.txt (line 26))
  Downloading email_validator-2.2.0-py3-none-any.whl.metadata (25 kB)
Collecting orjson<3.12.0,>=3.11.0 (from -r requirements.txt (line 29))
  Using cached orjson-3.11.1-cp313-cp313-win_amd64.whl.metadata (43 kB)
Collecting anyio<5.0.0,>=4.10.0 (from -r requirements.txt (line 32))
  Using cached anyio-4.10.0-py3-none-any.whl.metadata (4.0 kB)
Collecting httpx<0.29.0,>=0.28.0 (from -r requirements.txt (line 33))
  Using cached httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
Collecting cryptography<44.0.0,>=43.0.0 (from -r requirements.txt (line 36))
  Downloading cryptography-43.0.3-cp39-abi3-win_amd64.whl.metadata (5.4 kB)
Collecting rich<15.0.0,>=14.1.0 (from -r requirements.txt (line 39))
  Using cached rich-14.1.0-py3-none-any.whl.metadata (18 kB)
Collecting aiofiles<25.0.0,>=24.1.0 (from -r requirements.txt (line 42))
  Using cached aiofiles-24.1.0-py3-none-any.whl.metadata (10 kB)
Collecting python-dateutil<3.0.0,>=2.9.0 (from -r requirements.txt (line 45))
  Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
Collecting PyYAML<7.0.0,>=6.0.2 (from -r requirements.txt (line 48))
  Using cached PyYAML-6.0.2-cp313-cp313-win_amd64.whl.metadata (2.1 kB)
Collecting Pillow<12.0.0,>=11.3.0 (from -r requirements.txt (line 51))
  Using cached pillow-11.3.0-cp313-cp313-win_amd64.whl.metadata (9.2 kB)
Collecting websockets<16.0.0,>=15.0.0 (from -r requirements.txt (line 54))
  Using cached websockets-15.0.1-cp313-cp313-win_amd64.whl.metadata (7.0 kB)
Collecting Jinja2<4.0.0,>=3.1.6 (from -r requirements.txt (line 57))
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting MarkupSafe<4.0.0,>=3.0.2 (from -r requirements.txt (line 58))
  Using cached MarkupSafe-3.0.2-cp313-cp313-win_amd64.whl.metadata (4.1 kB)
Collecting click<9.0.0,>=8.2.0 (from -r requirements.txt (line 61))
  Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
Collecting typer<1.0.0,>=0.16.0 (from -r requirements.txt (line 62))
  Using cached typer-0.16.0-py3-none-any.whl.metadata (15 kB)
Collecting tqdm<5.0.0,>=4.67.0 (from -r requirements.txt (line 65))
  Using cached tqdm-4.67.1-py3-none-any.whl.metadata (57 kB)
Collecting colorama<0.5.0,>=0.4.6 (from -r requirements.txt (line 68))
  Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
Collecting packaging<26.0,>=25.0 (from -r requirements.txt (line 71))
  Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Collecting fsspec>=2025.7.0 (from -r requirements.txt (line 74))
  Using cached fsspec-2025.7.0-py3-none-any.whl.metadata (12 kB)
Collecting pydub<0.26.0,>=0.25.1 (from -r requirements.txt (line 77))
  Using cached pydub-0.25.1-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting h11<0.17.0,>=0.16.0 (from -r requirements.txt (line 80))
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting httpcore<2.0.0,>=1.0.9 (from -r requirements.txt (line 81))
  Using cached httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
Collecting semantic-version<3.0.0,>=2.10.0 (from -r requirements.txt (line 84))
  Using cached semantic_version-2.10.0-py2.py3-none-any.whl.metadata (9.7 kB)
Collecting tomlkit<0.14.0,>=0.13.3 (from -r requirements.txt (line 87))
  Using cached tomlkit-0.13.3-py3-none-any.whl.metadata (2.8 kB)
Collecting shellingham<2.0.0,>=1.5.4 (from -r requirements.txt (line 90))
  Using cached shellingham-1.5.4-py2.py3-none-any.whl.metadata (3.5 kB)
Collecting markdown-it-py<4.0.0,>=3.0.0 (from -r requirements.txt (line 93))
  Using cached markdown_it_py-3.0.0-py3-none-any.whl.metadata (6.9 kB)
Collecting mdurl<0.2.0,>=0.1.2 (from -r requirements.txt (line 94))
  Using cached mdurl-0.1.2-py3-none-any.whl.metadata (1.6 kB)
Collecting pygments<3.0.0,>=2.19.0 (from -r requirements.txt (line 97))
  Using cached pygments-2.19.2-py3-none-any.whl.metadata (2.5 kB)
Collecting filelock<4.0.0,>=3.18.0 (from -r requirements.txt (line 100))
  Using cached filelock-3.18.0-py3-none-any.whl.metadata (2.9 kB)
Collecting brotli<2.0.0,>=1.1.0 (from -r requirements.txt (line 103))
  Using cached Brotli-1.1.0-cp313-cp313-win_amd64.whl.metadata (5.6 kB)
Collecting audioop-lts<1.0.0,>=0.2.2 (from -r requirements.txt (line 106))
  Using cached audioop_lts-0.2.2-cp313-abi3-win_amd64.whl.metadata (2.0 kB)
Collecting ffmpy<0.7.0,>=0.6.1 (from -r requirements.txt (line 109))
  Using cached ffmpy-0.6.1-py3-none-any.whl.metadata (2.9 kB)
Collecting groovy<0.2.0,>=0.1.2 (from -r requirements.txt (line 112))
  Using cached groovy-0.1.2-py3-none-any.whl.metadata (6.1 kB)
Collecting huggingface-hub<1.0.0,>=0.34.0 (from -r requirements.txt (line 115))
  Using cached huggingface_hub-0.34.4-py3-none-any.whl.metadata (14 kB)
Collecting safehttpx<0.2.0,>=0.1.6 (from -r requirements.txt (line 118))
  Using cached safehttpx-0.1.6-py3-none-any.whl.metadata (4.2 kB)
Collecting ruff<0.13.0,>=0.12.8 (from -r requirements.txt (line 121))
  Using cached ruff-0.12.8-py3-none-win_amd64.whl.metadata (26 kB)
Collecting starlette<0.47.0,>=0.40.0 (from fastapi<0.116.0,>=0.115.0->-r requirements.txt (line 2))
  Downloading starlette-0.46.2-py3-none-any.whl.metadata (6.2 kB)
Collecting annotated-types>=0.6.0 (from pydantic<2.12.0,>=2.11.0->-r requirements.txt (line 4))
  Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.33.2 (from pydantic<2.12.0,>=2.11.0->-r requirements.txt (line 4))
  Using cached pydantic_core-2.33.2-cp313-cp313-win_amd64.whl.metadata (6.9 kB)
Collecting typing-inspection>=0.4.0 (from pydantic<2.12.0,>=2.11.0->-r requirements.txt (line 4))
  Using cached typing_inspection-0.4.1-py3-none-any.whl.metadata (2.6 kB)
Collecting pytz>=2020.1 (from pandas<2.4.0,>=2.3.0->-r requirements.txt (line 7))
  Using cached pytz-2025.2-py2.py3-none-any.whl.metadata (22 kB)
Collecting tzdata>=2022.7 (from pandas<2.4.0,>=2.3.0->-r requirements.txt (line 7))
  Using cached tzdata-2025.2-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting charset_normalizer<4,>=2 (from requests<2.33.0,>=2.32.0->-r requirements.txt (line 14))
  Using cached charset_normalizer-3.4.3-cp313-cp313-win_amd64.whl.metadata (37 kB)
Collecting idna<4,>=2.5 (from requests<2.33.0,>=2.32.0->-r requirements.txt (line 14))
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting gradio-client==1.11.1 (from gradio<5.43.0,>=5.42.0->-r requirements.txt (line 19))
  Using cached gradio_client-1.11.1-py3-none-any.whl.metadata (7.1 kB)
Collecting dnspython>=2.0.0 (from email-validator<3.0.0,>=2.0.0->-r requirements.txt (line 26))
  Downloading dnspython-2.7.0-py3-none-any.whl.metadata (5.8 kB)
Collecting sniffio>=1.1 (from anyio<5.0.0,>=4.10.0->-r requirements.txt (line 32))
  Using cached sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting cffi>=1.12 (from cryptography<44.0.0,>=43.0.0->-r requirements.txt (line 36))
  Using cached cffi-1.17.1-cp313-cp313-win_amd64.whl.metadata (1.6 kB)
Collecting six>=1.5 (from python-dateutil<3.0.0,>=2.9.0->-r requirements.txt (line 45))
  Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting httptools>=0.6.3 (from uvicorn[standard]<0.36.0,>=0.35.0->-r requirements.txt (line 3))
  Downloading httptools-0.6.4-cp313-cp313-win_amd64.whl.metadata (3.7 kB)
Collecting watchfiles>=0.13 (from uvicorn[standard]<0.36.0,>=0.35.0->-r requirements.txt (line 3))
  Downloading watchfiles-1.1.0-cp313-cp313-win_amd64.whl.metadata (5.0 kB)
Collecting pycparser (from cffi>=1.12->cryptography<44.0.0,>=43.0.0->-r requirements.txt (line 36))
  Using cached pycparser-2.22-py3-none-any.whl.metadata (943 bytes)
Downloading fastapi-0.115.14-py3-none-any.whl (95 kB)
Using cached uvicorn-0.35.0-py3-none-any.whl (66 kB)
Using cached pydantic-2.11.7-py3-none-any.whl (444 kB)
Using cached pydantic_core-2.33.2-cp313-cp313-win_amd64.whl (2.0 MB)
Using cached pandas-2.3.1-cp313-cp313-win_amd64.whl (11.0 MB)
Using cached numpy-2.3.2-cp313-cp313-win_amd64.whl (12.8 MB)
Using cached python_dotenv-1.1.1-py3-none-any.whl (20 kB)
Using cached requests-2.32.4-py3-none-any.whl (64 kB)
Using cached urllib3-2.5.0-py3-none-any.whl (129 kB)
Using cached gradio-5.42.0-py3-none-any.whl (59.7 MB)
Using cached gradio_client-1.11.1-py3-none-any.whl (324 kB)
Using cached typing_extensions-4.14.1-py3-none-any.whl (43 kB)
Using cached python_multipart-0.0.20-py3-none-any.whl (24 kB)
Downloading email_validator-2.2.0-py3-none-any.whl (33 kB)
Using cached orjson-3.11.1-cp313-cp313-win_amd64.whl (131 kB)
Using cached anyio-4.10.0-py3-none-any.whl (107 kB)
Using cached httpx-0.28.1-py3-none-any.whl (73 kB)
Downloading cryptography-43.0.3-cp39-abi3-win_amd64.whl (3.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.1/3.1 MB 12.7 MB/s  0:00:00
Using cached rich-14.1.0-py3-none-any.whl (243 kB)
Using cached aiofiles-24.1.0-py3-none-any.whl (15 kB)
Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
Using cached PyYAML-6.0.2-cp313-cp313-win_amd64.whl (156 kB)
Using cached pillow-11.3.0-cp313-cp313-win_amd64.whl (7.0 MB)
Using cached websockets-15.0.1-cp313-cp313-win_amd64.whl (176 kB)
Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Using cached MarkupSafe-3.0.2-cp313-cp313-win_amd64.whl (15 kB)
Using cached click-8.2.1-py3-none-any.whl (102 kB)
Using cached typer-0.16.0-py3-none-any.whl (46 kB)
Using cached tqdm-4.67.1-py3-none-any.whl (78 kB)
Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Using cached packaging-25.0-py3-none-any.whl (66 kB)
Using cached pydub-0.25.1-py2.py3-none-any.whl (32 kB)
Using cached h11-0.16.0-py3-none-any.whl (37 kB)
Using cached httpcore-1.0.9-py3-none-any.whl (78 kB)
Using cached semantic_version-2.10.0-py2.py3-none-any.whl (15 kB)
Using cached tomlkit-0.13.3-py3-none-any.whl (38 kB)
Using cached shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Using cached markdown_it_py-3.0.0-py3-none-any.whl (87 kB)
Using cached mdurl-0.1.2-py3-none-any.whl (10.0 kB)
Using cached pygments-2.19.2-py3-none-any.whl (1.2 MB)
Using cached filelock-3.18.0-py3-none-any.whl (16 kB)
Using cached Brotli-1.1.0-cp313-cp313-win_amd64.whl (358 kB)
Using cached audioop_lts-0.2.2-cp313-abi3-win_amd64.whl (30 kB)
Using cached ffmpy-0.6.1-py3-none-any.whl (5.5 kB)
Using cached groovy-0.1.2-py3-none-any.whl (14 kB)
Using cached huggingface_hub-0.34.4-py3-none-any.whl (561 kB)
Using cached safehttpx-0.1.6-py3-none-any.whl (8.7 kB)
Using cached ruff-0.12.8-py3-none-win_amd64.whl (12.7 MB)
Using cached charset_normalizer-3.4.3-cp313-cp313-win_amd64.whl (107 kB)
Using cached idna-3.10-py3-none-any.whl (70 kB)
Downloading starlette-0.46.2-py3-none-any.whl (72 kB)
Using cached certifi-2025.8.3-py3-none-any.whl (161 kB)
Using cached fsspec-2025.7.0-py3-none-any.whl (199 kB)
Using cached annotated_types-0.7.0-py3-none-any.whl (13 kB)
Using cached cffi-1.17.1-cp313-cp313-win_amd64.whl (182 kB)
Downloading dnspython-2.7.0-py3-none-any.whl (313 kB)
Downloading httptools-0.6.4-cp313-cp313-win_amd64.whl (87 kB)
Using cached pytz-2025.2-py2.py3-none-any.whl (509 kB)
Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
Using cached typing_inspection-0.4.1-py3-none-any.whl (14 kB)
Using cached tzdata-2025.2-py2.py3-none-any.whl (347 kB)
Downloading watchfiles-1.1.0-cp313-cp313-win_amd64.whl (292 kB)
Using cached pycparser-2.22-py3-none-any.whl (117 kB)
Installing collected packages: pytz, pydub, brotli, websockets, urllib3, tzdata, typing-extensions, tomlkit, sniffio, six, shellingham, semantic-version, ruff, PyYAML, python-multipart, python-dotenv, pygments, pycparser, Pillow, packaging, orjson, numpy, mdurl, MarkupSafe, idna, httptools, h11, groovy, fsspec, filelock, ffmpy, dnspython, colorama, charset_normalizer, certifi, audioop-lts, annotated-types, aiofiles, typing-inspection, tqdm, requests, python-dateutil, pydantic-core, markdown-it-py, Jinja2, httpcore, email-validator, click, cffi, anyio, watchfiles, uvicorn, starlette, rich, pydantic, pandas, huggingface-hub, httpx, cryptography, typer, safehttpx, gradio-client, fastapi, gradio
Successfully installed Jinja2-3.1.6 MarkupSafe-3.0.2 Pillow-11.3.0 PyYAML-6.0.2 aiofiles-24.1.0 annotated-types-0.7.0 anyio-4.10.0 audioop-lts-0.2.2 brotli-1.1.0 certifi-2025.8.3 cffi-1.17.1 charset_normalizer-3.4.3 click-8.2.1 colorama-0.4.6 cryptography-43.0.3 dnspython-2.7.0 email-validator-2.2.0 fastapi-0.115.14 ffmpy-0.6.1 filelock-3.18.0 fsspec-2025.7.0 gradio-5.42.0 gradio-client-1.11.1 groovy-0.1.2 h11-0.16.0 httpcore-1.0.9 httptools-0.6.4 httpx-0.28.1 huggingface-hub-0.34.4 idna-3.10 markdown-it-py-3.0.0 mdurl-0.1.2 numpy-2.3.2 orjson-3.11.1 packaging-25.0 pandas-2.3.1 pycparser-2.22 pydantic-2.11.7 pydantic-core-2.33.2 pydub-0.25.1 pygments-2.19.2 python-dateutil-2.9.0.post0 python-dotenv-1.1.1 python-multipart-0.0.20 pytz-2025.2 requests-2.32.4 rich-14.1.0 ruff-0.12.8 safehttpx-0.1.6 semantic-version-2.10.0 shellingham-1.5.4 six-1.17.0 sniffio-1.3.1 starlette-0.46.2 tomlkit-0.13.3 tqdm-4.67.1 typer-0.16.0 typing-extensions-4.14.1 typing-inspection-0.4.1 tzdata-2025.2 urllib3-2.5.0 uvicorn-0.35.0 watchfiles-1.1.0 websockets-15.0.1        
(venv) PS C:\Users\DELL\Downloads\IEEE Techsangam\demo dashboard\patient-dashboard\agent> python -c "import requests; print('✅ Success!')"
>> python test_installation.py
✅ Success!
🚀 Agent Companion Installation Test
========================================
Python version: 3.13.6 (tags/v3.13.6:4e66535, Aug  6 2025, 14:36:00) [MSC v.1944 64 bit (AMD64)]
Python executable: C:\Users\DELL\Downloads\IEEE Techsangam\demo dashboard\patient-dashboard\agent\venv\Scripts\python.exe
========================================
🧪 Testing module imports...
  ❌ fastapi: FAILED - cannot import name 'create_model' from 'pydantic' (C:\Users\DELL\Downloads\IEEE Techsangam\demo dashboard\patient-dashboard\agent\pydantic\__init__.py)
  ✅ uvicorn: ASGI server
  ✅ pydantic: Data validation
  ✅ gradio: Web interface
  ✅ requests: HTTP client
  ✅ pandas: Data processing
  ✅ dotenv: Environment variables
  ✅ typing_extensions: Type hints

🏠 Testing local module imports...
  ✅ models.agent_companion_models: Data models
  ✅ services.agent_companion_service: Agent service
  ✅ services.llm_service: LLM service
  ✅ services.journal_data_service: Journal service

⚙️ Testing basic functionality...
  ✅ Pydantic models working correctly
  ✅ Chat message model working correctly
  ✅ Conversation model working correctly

🔧 Testing service instantiation...
Warning: CSV file not found at mock_user_journal_data.csv
Warning: CSV file not found at mock_user_journal_data_with_questions.csv
  ✅ Journal data service instantiated
  ✅ LLM service instantiated
Warning: CSV file not found at mock_user_journal_data.csv
Warning: CSV file not found at mock_user_journal_data_with_questions.csv
  ✅ Agent companion service instantiated

🌐 Testing Gradio app...
Warning: CSV file not found at mock_user_journal_data.csv
Warning: CSV file not found at mock_user_journal_data_with_questions.csv
  ✅ Gradio app imported successfully

📊 Test Summary:
====================
❌ Failed external imports: fastapi
✅ All local modules imported successfully
✅ Basic functionality tests passed
✅ Service instantiation tests passed
✅ Gradio app import test passed

❌ Some tests failed. Please check the errors above.

Troubleshooting tips:
1. Make sure you're in the activated virtual environment
2. Try reinstalling dependencies: pip install -r requirements.txt
3. Check that all files are in the correct locations
(venv) PS C:\Users\DELL\Downloads\IEEE Techsangam\demo dashboard\patient-dashboard\agent>
and tell me whats going wrong here?