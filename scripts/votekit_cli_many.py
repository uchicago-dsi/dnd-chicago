import click
import json
import jsonlines as jl
import votekit.elections as elec
from votekit import PreferenceProfile
import votekit.ballot_generator as bg
import warnings
import random

warnings.filterwarnings("ignore")

ELECTION_TYPES = {
    "stv": elec.STV,
    "borda": elec.Borda,
    "plurality": elec.Plurality,
}

BG_TYPES = {
    "slate_pl": bg.slate_PlackettLuce,
    "slate_bt": bg.slate_BradleyTerry,
    "cambridge": bg.CambridgeSampler,
}


def run_election(
    ballot_generator: str,
    num_voters: int,
    num_seats: int,
    ballot_generator_kwargs: dict,
    election_type: str,
    num_iterations: int,
    output_file: click.Path,
):
    with jl.open(output_file, "w") as writer:
        for _ in range(num_iterations):
            profile = (
                BG_TYPES[ballot_generator]
                .from_params(**ballot_generator_kwargs)
                .generate_profile(num_voters)
            )
            assert isinstance(profile, PreferenceProfile)

            election: elec.Election = ELECTION_TYPES[election_type](
                profile, m=num_seats, tiebreak="random"
            )
            winners = winners = [next(iter(s)) for s in election.get_elected() if s]
            writer.write({"winners": winners})


# def run_election(
#     ballot_generator: str,
#     num_voters: int,
#     num_seats: int,
#     ballot_generator_kwargs: dict,
#     election_type: str,
#     num_iterations: int,
#     output_file: click.Path,
# ):
#     with jl.open(output_file, "w") as writer:
#         for _ in range(num_iterations):
#             profile = (
#                 BG_TYPES[ballot_generator]
#                 .from_params(**ballot_generator_kwargs)
#                 .generate_profile(num_voters)
#             )
#             assert isinstance(profile, PreferenceProfile)

#             # Random bad constructor
#             if random.random() < 0.01:
#                 election: elec.Election = ELECTION_TYPES[election_type](profile, m=1000)
#             election: elec.Election = ELECTION_TYPES[election_type](
#                 profile, m=num_seats, tiebreak="random"
#             )
#             winners = winners = [next(iter(s)) for s in election.get_elected() if s]
#             writer.write({"winners": winners})


# ==============================================
# Now make a little CLI to wrap this function in
# ==============================================


@click.command()
@click.option(
    "--ballot-generator",
    type=click.Choice(list(BG_TYPES.keys()), case_sensitive=False),
    default="cambridge",
    help="The type of ballot generator to use.",
)
@click.option(
    "--num-voters",
    type=int,
    default=1000,
    help="The number of voters to generate.",
)
@click.option(
    "--num-seats",
    type=int,
    default=1,
    help="The number of seats to fill in the election.",
)
@click.option(
    "--election-type",
    type=click.Choice(list(ELECTION_TYPES.keys()), case_sensitive=False),
    default="stv",
    help="The type of election to run.",
)
@click.option(
    "--ballot-generator-kwargs-settings-file",
    "--bg-settings",
    type=click.Path(exists=True),
    default="NO SETTINGS FILE GIVEN",
    help="Additional keyword arguments for the ballot generator, as a JSON string.",
)
@click.option(
    "--num-iterations",
    type=int,
    default=1000,
    help="Number of iterations for the election process.",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Path to save the election results.",
)
def run_election_cli(
    ballot_generator: str,
    num_voters: int,
    num_seats: int,
    election_type: str,
    ballot_generator_kwargs_settings_file: str,
    num_iterations: int,
    output_file: click.Path,
):
    with open(ballot_generator_kwargs_settings_file, "r") as f:
        ballot_generator_kwargs = json.load(f)

    if ballot_generator_kwargs is None:
        ballot_generator_kwargs = {}

    run_election(
        ballot_generator=ballot_generator,
        num_voters=num_voters,
        num_seats=num_seats,
        ballot_generator_kwargs=ballot_generator_kwargs,
        election_type=election_type,
        num_iterations=num_iterations,
        output_file=output_file,
    )


if __name__ == "__main__":
    run_election_cli()
