library(lubridate)
library(ggplot2)
library(scales)

data <- read.csv('rate_history.csv', col.names=c('timestamp', 'type', 'rate'))

data$timestamp <- ymd_hms(as.character(data$timestamp))
data$timestamp <- as.Date(data$timestamp)

data <- subset(data, type %in% c("30-Year Fixed Rate", "15-Year Fixed Rate", "5/1 ARM", "7/1 ARM"))

qplot(timestamp, rate, data=data, color=type, geom="line") +
  geom_point() +
  scale_y_continuous(labels=percent) +
  scale_x_date(date_breaks = "1 month", date_minor_breaks = "1 week", date_labels = "%B") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  labs(x="date", y="interest rate", title="historic interest rates from www.wellsfargo.com/mortgage/rates/")

ggsave("wfc_historic_rates.png", height=5, width=8)