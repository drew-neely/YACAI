#include <assert.h>

#include "../minimax.h"

#include "score-tests.h"

namespace {

template <typename Eval_t>
void expect_order(const Score<Eval_t>& better, const Score<Eval_t>& worse) {
    assert(better > worse);
    assert(!(better < worse));
    assert(worse < better);
    assert(!(worse > better));
}

template <typename Eval_t>
void expect_equivalent(const Score<Eval_t>& lhs, const Score<Eval_t>& rhs) {
    assert(!(lhs < rhs));
    assert(!(rhs < lhs));
    assert(!(lhs > rhs));
    assert(!(rhs > lhs));
}

} // namespace

void run_score_tests() {
    using ScoreT = Score<int16_t>;

    ScoreT higher_eval{200, 0, 4};
    ScoreT lower_eval{150, 0, 4};
    expect_order(higher_eval, lower_eval);

    ScoreT fast_white_mate{0, 2, 4};
    ScoreT slow_white_mate{0, 4, 4};
    expect_order(fast_white_mate, slow_white_mate);

    ScoreT slow_black_mate{0, -5, 4};
    ScoreT fast_black_mate{0, -2, 4};
    expect_order(slow_black_mate, fast_black_mate);

    ScoreT forced_mate{0, 3, 4};
    ScoreT big_eval{5000, 0, 4};
    expect_order(forced_mate, big_eval);

    ScoreT solid_eval{25, 0, 4};
    ScoreT looming_black_mate{0, -1, 4};
    expect_order(solid_eval, looming_black_mate);

    ScoreT tie_eval{120, 0, 4};
    ScoreT tie_eval_copy{120, 0, 7};
    expect_equivalent(tie_eval, tie_eval_copy);

    printf("SCORE TESTS PASSED\n");
}
