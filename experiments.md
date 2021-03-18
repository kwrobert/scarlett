# Experiment 1: first_test

## Summary and Goal 

I tried to keep things simple and get to results as quickly as I could. I
finetuned the 335M model to start.

To create a single training sample, I took the title of the article and placed
it as the first line of the text body, added a newline, then appended the body
of the article in plain text. The article titles contain the name of the store
the article is written for and the "page template" used to generate the
article. A "page template" is an internal concept at CCA Global, they basically
have templates for the structure of pages for advertising different types of products their
stores offer ("Area Rugs", "Vinyl Flooring", "Kitchen and Bathroom Flooring",
etc). Because the page template name contains a lot of contextual information
indicating what the article is about, by putting the title as the first line I
was hoping the model would learn to generate articles about the correct topic,
with reference to the location/name of the store, and  conforming to the
structure of the page template just from looking at the title.

Then, we can provide the title of the article as the prompt/prefix when generating new samples and hopefully things turn out well.

## Results

This actually worked surprisingly well! The neural net learned to generate
pages with structure resembling the structure of the page template, refers to
the name of the store embedded in the title within the body of the article, and
generates a body with the correct topic based on the page template name
embedded in the title. The sentences are all grammatically correct, but there
are a few instances where the sentences don't make sense. For example, a sample
generated from a carpet page template prompt refers to a carpet as "glazed" but
glazing is only done to tile flooring.

## New Things To Try

1. Is it possible, with more examples, for the model to correlate certain concepts about a product specifically with that product (so, fix the "glazed carpets" issue above)?
2. If we have enough training data for each page template, could we train a separate model for each template and get better, more conceptually accurate results?
3. How do we collect more training data?
4. Articles must be at least 300 words in length, but are usually around 500 words. How can we make the model generate longer samples?
5. Will larger models (i.e 774M) perform better?

# Experiment 2: first_test_774M

## Summary and Goal 

Basically the same exact test as Experiment 1 but with a larger model just to
see if it improves results

## Results

Hit out of memory error. Tried setting `multi_gpu=True` and didn't hit OOM errors but keep getting 'nans' in the training loss. 

## New Things To Try

Dunno, opened an issue on Github and we'll see what comes of it.

# Experiment 3: experiment_3_355M

## Summary and Goal 

Experiment 1 went pretty well, but I think with labeled training data we might get better results. To this end, instead of just chucking the raw text into the model I created writing samples with the following structure: 

```
[LABELS] 

title: Wrucks Carpet One Floor & Home Backsplash Tile Page Update

store_name: Wrucks Carpet One Floor & Home

store_location: Wasilla United States

page_template: Backsplash Tile Page Update

keywords: stone tile backsplash:tile samples

[BODY]

<article body here>
```

To get the store location, I used the `geography` Python package to do automatic location extraction from the article body, and just included all locations that were in the United States or Canada (crude, but I don't want to spend days on data preprocessing). Keyword are really "keywords and phrases" and came from a list of keywords files that I used to build a "keyword corpus". The store name I had to do a little bit of string-processing-tap-dancing to get right, and it's still a bit crude. The title was each and the page template is the title minus the store name.

My hope is that by training the model with this structured data, the model will learn to make correlations between the metadata in the labels with parts of the body. We can provide the LABELS section as a prefix when generating new samples and hopefully get better results. 

## Results

## New Things To Try
