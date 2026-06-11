import numpy as np
import scipy.stats as stats


class SignificanceCalc:

    def calculate(
        self,
        control_metrics: list,
        variant_metrics: list,
        alpha: float = 0.05
    ) -> dict:

        control = np.array(control_metrics)
        variant = np.array(variant_metrics)

        if len(control) < 10 or len(variant) < 10:
            return {
                "significant": False,
                "reason": "insufficient_samples"
            }

        # Welch t-test
        t_stat, p_value = stats.ttest_ind(
            control,
            variant,
            equal_var=False
        )

        # Cohen's d (effect size)
        pooled_std = np.sqrt(
            (np.var(control) + np.var(variant)) / 2
        )

        effect_size = (
            np.mean(variant) - np.mean(control)
        ) / (pooled_std + 1e-9)

        return {
            "t_stat": float(t_stat),
            "p_value": float(p_value),
            "significant": p_value < alpha,
            "effect_size": float(effect_size),
            "control_mean": float(np.mean(control)),
            "variant_mean": float(np.mean(variant))
        }