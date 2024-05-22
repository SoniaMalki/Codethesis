import { Component, Input, OnChanges, OnDestroy, SimpleChanges } from '@angular/core';
import { NbThemeService } from '@nebular/theme';
import { takeWhile } from 'rxjs/operators';
import { LayoutService } from '../../../../@core/utils/layout.service';

@Component({
  selector: 'ngx-country-orders-chart',
  styleUrls: ['./country-orders-chart.component.scss'],
  template: `
    <div class="header">
      <span class="caption">{{caption}}</span>
    </div>
    <div echarts
         [options]="option"
         class="echart"
         (chartInit)="onChartInit($event)">
    </div>
  `,
})
export class CountryOrdersChartComponent implements OnDestroy, OnChanges {

  @Input() caption: string;
  @Input() countryName: string;
  @Input() data: number[];
  @Input() maxValue: number;
  @Input() labels: string[];
  @Input() horizontal: boolean = false;

  private alive = true;

  option: any = {};
  echartsInstance;

  constructor(private theme: NbThemeService,
              private layoutService: LayoutService) {
    this.layoutService.onSafeChangeLayoutSize()
      .pipe(
        takeWhile(() => this.alive),
      )
      .subscribe(() => this.resizeChart());
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.data && !changes.data.isFirstChange() && this.echartsInstance) {
      this.echartsInstance.setOption({
        series: [
          {
            data: this.data.map(v => this.maxValue),
          },
          {
            data: this.data,
          },
          {
            data: this.data,
          },
        ],
      });
    }

    // Re-initialize chart options when input changes
    if (changes.horizontal && !changes.horizontal.isFirstChange()) {
      this.initChartOptions();
      if (this.echartsInstance) {
        this.echartsInstance.setOption(this.option, true);
      }
    }
  }

  initChartOptions() {
    this.theme.getJsTheme()
      .pipe(takeWhile(() => this.alive))
      .subscribe(config => {
        const countriesTheme: any = config.variables.countryOrders;

        const xAxisOptions = {
          axisLabel: {
            color: countriesTheme.chartAxisTextColor,
            fontSize: '13',
          },
          axisLine: {
            lineStyle: {
              color: countriesTheme.chartAxisLineColor,
              width: '2',
            },
          },
          axisTick: {
            show: false,
          },
          splitLine: {
            lineStyle: {
              color: countriesTheme.chartAxisSplitLine,
              width: '1',
            },
          },
        };

        const yAxisOptions = {
          axisLabel: {
            color: countriesTheme.chartAxisTextColor,
            fontSize: '13',
          },
          axisLine: {
            lineStyle: {
              color: countriesTheme.chartAxisLineColor,
              width: '2',
            },
          },
          axisTick: {
            show: false,
          },
        };

        this.option = Object.assign({}, {
          grid: {
            left: '3%',
            right: '3%',
            bottom: '3%',
            top: '3%',
            containLabel: true,
          },
          xAxis: this.horizontal ? xAxisOptions : {
            ...xAxisOptions,
            data: this.labels,
          },
          yAxis: this.horizontal ? {
            ...yAxisOptions,
            data: this.labels,
          } : yAxisOptions,
          series: [
            { // For shadow
              type: 'bar',
              data: this.data.map(v => this.maxValue),
              cursor: 'default',
              itemStyle: {
                normal: {
                  color: countriesTheme.chartInnerLineColor,
                },
                opacity: 1,
              },
              barWidth: '10%',
              barGap: '-100%',
              barCategoryGap: '30%',
              animation: false,
              z: 1,
              ...(this.horizontal ? {} : { xAxisIndex: 0 }),
            },
            { // For bottom line
              type: 'bar',
              data: this.data,
              cursor: 'default',
              itemStyle: {
                normal: {
                  color: countriesTheme.chartLineBottomShadowColor,
                },
                opacity: 1,
              },
              barWidth: '10%',
              barGap: '-100%',
              barCategoryGap: '30%',
              z: 2,
              ...(this.horizontal ? {} : { xAxisIndex: 0 }),
            },
            {
              type: 'bar',
              barWidth: '27%',
              data: this.data,
              cursor: 'default',
              itemStyle: {
                normal: {
                  color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [{
                    offset: 0,
                    color: countriesTheme.chartGradientFrom,
                  }, {
                    offset: 1,
                    color: countriesTheme.chartGradientTo,
                  }]),
                },
              },
              z: 3,
              ...(this.horizontal ? {} : { xAxisIndex: 0 }),
            },
          ],
        });
      });
  }

  onChartInit(ec) {
    this.echartsInstance = ec;

    this.initChartOptions();
  }

  resizeChart() {
    if (this.echartsInstance) {
      this.echartsInstance.resize();
    }
  }

  ngOnDestroy() {
    this.alive = false;
  }

}
