import os
from datetime import datetime
import gpt_2_simple as gpt2


def main():

    pages_to_gen = [
        # "Burlington Carpet One Floor & Home Custom Area Rugs",
        # "Hosner Carpet One Floor & Home Custom Area Rugs",
        # "Skawg Brothers Carpet One Floor & Home Kitchen and Bathroom Flooring",
        # "I-Five Carpet One Floor & Home Kitchen and Bathroom Tile"
        "Carpet Guide"
    ]
    # gen_file = "generated_samples/gpt2_gentext_{:%Y%m%d_%H%M%S}.txt".format(
    #     datetime.utcnow()
    # )
    run_name = "untrained_355M"
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name=run_name)
    # gpt2.generate(sess, run_name='first_test', prefix="Luxury Vinyl Plank Flooring")
    prefix = """
Raven Labs

Raven labs is the latest emerging company in Manchester NH. They utilize the latest technology and provide custom solutions using unique problems. With onboard engineers specializing in AI, Software engineering, Electo-Mechanical Engineering, and Production design they are a one stop shop to solve the toughest problems without breaking the bank.
    """
    fname = "raven_test.txt"
    gen_file = os.path.join("generated_samples", fname)
    gpt2.generate_to_file(
        sess,
        prefix=prefix,
        destination_path=gen_file,
        # length=500,
        temperature=0.7,
        nsamples=5,
        batch_size=1,
        run_name=run_name,
    )


if __name__ == "__main__":
    main()
