library("ggplot2")
library("dplyr")
options(scipen = 999)

for (obs in c(1)) {
    for (hops in c(1, 2, 3)) {
        for (d_size in c(1, 1000, 100000)) {
            for (e_type in c("dynamic", "total")) {
                d <- read.csv(glue::glue("e_{e_type}.csv"))
                d<-d %>% filter(n_obs == obs)
                d<-d %>% filter(n_hops == hops)
                d<-d %>% filter(data_size == d_size)
                unit <- if(e_type == "dynamic") "J" else "kJ"
                if (e_type == "dynamic") {
                    color <- function(){scale_fill_manual(values = c("#00AFBB", "#E7B800", "#FC4E07"))}
                }
                else {
                    color <- function(){scale_fill_manual(values = c("#b1c470", "#8370c4", "#FC4E07"))}
                }
                ggplot(d, aes(x=reorder(n_deps, srv_tplgy_index), y=energy_mean, fill=type_comms, label=sprintf("%0.2f", energy_mean))) +
                    geom_bar(color="black", stat = "identity", position = "dodge") +
                    geom_errorbar(position=position_dodge(0.9), aes(ymin=energy_mean - energy_std, ymax=energy_mean + energy_std), width=.2, linewidth=1) +
                    geom_text(aes(y=min(energy_mean)/2), fontface="bold", position=position_dodge(width=0.9)) +
                    ylab(glue::glue("Accumulated energy consumption ({unit})")) +
                    theme(axis.text.y = element_text()) +
                    xlab("Number of dependencies per observer/aggregator") +
                    labs(fill=glue::glue("Nb observers: {obs}, Nb hops: {hops}, Data size: {d_size}, Type comms:")) +
                    theme(legend.position="top", legend.text=element_text(size=15), legend.title=element_text(size=15), axis.text=element_text(size=15), axis.title.y=element_text(size=15, vjust=2.5)) +
                    color()
                ggsave(glue::glue("plots/{hops}/{e_type}-{obs}-{hops}-{d_size}.pdf"), width=9, height=6)
            }
        }
    }
}
warnings()
