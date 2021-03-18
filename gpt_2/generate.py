import os
from datetime import datetime
import gpt_2_simple as gpt2


def main():

    pages_to_gen = [
        # "Burlington Carpet One Floor & Home Custom Area Rugs",
        # "Hosner Carpet One Floor & Home Custom Area Rugs",
        # "Skawg Brothers Carpet One Floor & Home Kitchen and Bathroom Flooring",
        # "I-Five Carpet One Floor & Home Kitchen and Bathroom Tile"
        # "Types of Luxury Vinyl",
        # "Waterproof Vinyl Page",
        "Stain Resistant Carpet Page",
        "Types of Vinyl Page",
        "Commercial Flooring Page"
        # "Stair Runner Carpet",
        # "Types of Carpet",
        # "Waterproof Luxury Vinyl",
        # "Custom Area Rugs"
        "Carpet Guide Page"
    ]
    
    # gen_file = "generated_samples/gpt2_gentext_{:%Y%m%d_%H%M%S}.txt".format(
    #     datetime.utcnow()
    # )
    run_name = "first_test"
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name=run_name)
    # gpt2.generate(sess, run_name='first_test', prefix="Luxury Vinyl Plank Flooring")
    for prefix in pages_to_gen:
        fname = prefix.replace(" ", "_") + ".txt"
        print(f"Saving samples for prefix {prefix} to {fname}")
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
