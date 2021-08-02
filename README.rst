Scarlett
========

This is me playing around with some GPT-2 models to automated generating
marketing content for my girlfriend. We have affectionately named the model
Scarlett after Scarlett Johansen's voice-role in the movie Her.

.. contents:: **Table of Contents**
    :backlinks: none

Installation
------------

gpt-2 is distributed on `PyPI <https://pypi.org>`_ as a universal
wheel and is available on Linux/macOS and Windows and supports
Python 2.7/3.5+ and PyPy.

.. code-block:: bash

    $ pip install gpt-2


Usage
-----

The `prefix` argument to `generate` is where you can provide a starting prompt to
the text generation. The generated text is a "prediction" of what is most
likely to follow the given prefix.

SO, we could create a "prefix" for each article that looks like 

```
Title: <title of article goes here>
Location: <location of store article is written for>
Subject keywords: <keywords describing subject of the article goes here>
```

And pass that to the `generate` to get some meaningful, store-specific results.

License
-------

gpt-2 is distributed under the terms of both

- `MIT License <https://choosealicense.com/licenses/mit>`_
- `Apache License, Version 2.0 <https://choosealicense.com/licenses/apache-2.0>`_

at your option.
