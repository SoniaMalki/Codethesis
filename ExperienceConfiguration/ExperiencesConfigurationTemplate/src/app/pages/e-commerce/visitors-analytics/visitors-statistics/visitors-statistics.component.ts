import { AfterViewInit, Component, Input, OnDestroy } from '@angular/core';
import { NbThemeService } from '@nebular/theme';
import { delay, takeWhile } from 'rxjs/operators';
import { LayoutService } from '../../../../@core/utils/layout.service';

@Component({
  selector: 'ngx-visitors-statistics',
  styleUrls: ['./visitors-statistics.component.scss'],
  templateUrl: './visitors-statistics.component.html',
})
export class ECommerceVisitorsStatisticsComponent implements AfterViewInit, OnDestroy {

  private alive = true;
  private iconColors = ['#42A5F5', '#66BB6A', '#FFA726', '#FF5722', '#AB47BC', '#1aff38', '#e182ff', '#ff82a4', '#fff143', '#8891ff', '#3b3b3b', '#7aff7f', '#d3d3d3', '#00b181']

  private _value: { [key: string]: number };
  @Input()
  set value(data: { [key: string]: number }) {
    this._value = data;
    this.processInputData();
    this.setOptions();
  }
  get value() {
    return this._value;
  }

  processedData: { name: string, value: number }[];
  option: any = {};
  chartLegend: { iconColor: string; title: string }[];
  echartsIntance: any;

  constructor(private theme: NbThemeService,
              private layoutService: LayoutService) {
    this.layoutService.onSafeChangeLayoutSize()
      .pipe(takeWhile(() => this.alive))
      .subscribe(() => this.resizeChart());
  }

  ngAfterViewInit() {
    this.theme.getJsTheme()
      .pipe(
        takeWhile(() => this.alive),
        delay(1),
      )
      .subscribe(config => {
        const variables: any = config.variables;
        const visitorsPieLegend: any = config.variables.visitorsPieLegend;

        this.setLegendItems();
      });
  }

  processInputData() {
    this.processedData = Object.entries(this._value).map(([name, value]) => ({ name, value }));
  }

  setLegendItems() {
    this.chartLegend = this.processedData.map((item, index) => {
      const percentage = ((item.value / 100) * 100).toFixed(0);
      return {
        iconColor: this.iconColors[index],
        title: `${item.name} (${percentage}%)`,
      };
    });
  }

  setOptions() {
    this.theme.getJsTheme().pipe(
      takeWhile(() => this.alive),
      delay(1),
    ).subscribe(config => {
      const variables: any = config.variables;
      const visitorsPie: any = variables.visitorsPie;
      const totalValue = this.getTotalVisitors();

      this.option = {
        tooltip: {
          trigger: 'item',
          formatter: '',
        },
        series: [
          {
            name: ' ',
            clockWise: true,
            hoverAnimation: false,
            type: 'pie',
            center: ['50%', '50%'],
            radius: ['0%', '80%'], 
            data: this.processedData.map((item, index) => ({
              value: item.value,
              name: ' ',
              label: {
                normal: {
                  position: 'center',
                  formatter: '',
                  textStyle: {
                    fontSize: '22',
                    fontFamily: variables.fontSecondary,
                    fontWeight: '600',
                    color: variables.fgHeading,
                  },
                },
              },
              tooltip: {
                show: false,
              },
              itemStyle: {
                normal: {
                  color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    {
                      offset: 0,
                      color: this.iconColors[index],
                    },
                    {
                      offset: 1,
                      color: this.iconColors[index],
                    },
                  ]),
                  shadowColor: visitorsPie.firstPieShadowColor || '#000',
                  shadowBlur: 0,
                  shadowOffsetX: 0,
                  shadowOffsetY: 3,
                },
              },
              hoverAnimation: false,
            })),
          },
          {
            name: ' ',
            clockWise: true,
            hoverAnimation: false,
            type: 'pie',
            center: ['50%', '50%'],
            radius: ['0%', '80%'], 
            data: [
              {
                value: totalValue,
                name: ' ',
                label: {
                  normal: {
                    position: 'center',
                    formatter: '',
                    textStyle: {
                      fontSize: '22',
                      fontFamily: variables.fontSecondary,
                      fontWeight: '600',
                      color: variables.fgHeading,
                    },
                  },
                },
                tooltip: {
                  show: false,
                },
                itemStyle: {
                  normal: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1),
                  },
                },
                hoverAnimation: false,
              },
              {
                value: 100 - totalValue,
                name: ' ',
                tooltip: {
                  show: false,
                },
                label: {
                  normal: {
                    position: 'inner',
                  },
                },
                itemStyle: {
                  normal: {
                    color: visitorsPie.layoutBg || '#ffffff',
                  },
                },
              },
            ],
          },
        ],
      };
    });
  }

  getTotalVisitors(): number {
    return this.processedData.reduce((sum, item) => sum + item.value, 0);
  }

  onChartInit(echarts) {
    this.echartsIntance = echarts;
  }

  resizeChart() {
    if (this.echartsIntance) {
      this.echartsIntance.resize();
    }
  }

  ngOnDestroy() {
    this.alive = false;
  }
}
