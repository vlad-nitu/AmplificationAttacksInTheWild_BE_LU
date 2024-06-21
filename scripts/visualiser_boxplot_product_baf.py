from visualiser_boxplot_vendor_or_product_DNS_base import preprocess_data, draw_boxplot

if __name__ == "__main__":
    box_plots = preprocess_data('product', 5)
    draw_boxplot('product', box_plots)

