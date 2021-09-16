FROM tensorflow/tensorflow:1.15.5-gpu-py3-jupyter 
RUN pip3 install --upgrade pip
RUN pip3 install gpt-2-simple opyrator
WORKDIR /tf/code/gpt_2
RUN mkdir -p /tf/code/config/matplotlib
ENV MPLCONFIGDIR=/tf/code/config/matplotlib
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

EXPOSE 8051

CMD ["opyrator", "launch-ui", "opyrator_ui:generate_prompts", "--port", "8051"]
