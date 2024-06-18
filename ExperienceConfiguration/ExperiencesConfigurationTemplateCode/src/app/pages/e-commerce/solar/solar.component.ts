import { delay } from 'rxjs/operators';
import { AfterViewInit, Component, Input, OnDestroy } from '@angular/core';
import { NbThemeService } from '@nebular/theme';

declare const echarts: any;

@Component({
    selector: 'ngx-solar',
    styleUrls: ['./solar.component.scss'],
    template: `
    <nb-card size="tiny" class="solar-card">
        <nb-card-body class="card-body" [ngStyle]="{'--card-bg-color': cardColor}">
            <div class="inner-body">
                <div class="title">{{title}}</div>
                <div echarts [options]="option" class="echart"></div>
                <div class="info">
                    <div class="h6 value">{{labelText}}</div>
                    <div class="details subtitle-2">
                        {{secondaryText}}
                    </div>
                </div>
            </div>
        </nb-card-body>
    </nb-card>
    <style>
        .card-body::before {
            content: "";
            display: block;
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 5px;
            background-color: var(--card-bg-color);
            border-radius: 0;
        }
    </style>
    `,
})
export class SolarComponent implements AfterViewInit, OnDestroy {

    @Input() title;
    @Input() labelText;
    @Input() secondaryText;
    @Input() totalLabel;
    @Input() percentage;
    @Input() current;
    @Input() total;
    @Input() cardColor;
    @Input() centerText: string;

    @Input()
    set chartValue(value: number) {
        if (this.option.series) {
            this.option.series[0].data[0].value = value;
            this.option.series[0].data[1].value = 100 - value;
        }
    }

    option: any = {};
    themeSubscription: any;

    constructor(private theme: NbThemeService) {}

    ngAfterViewInit() {
        this.themeSubscription = this.theme.getJsTheme().pipe(delay(1)).subscribe(config => {
            const solarTheme: any = config.variables.solar;
            const innerRadius = '63%'; // Adjust as needed
            const outerRadius = '78%'; // Adjust as needed

            const displayText = this.centerText || `${this.percentage}%`;

            this.option = {
                tooltip: {
                    trigger: 'item',
                    formatter: '{a} <br/>{b} : {c} ({d}%)',
                },
                series: [
                    {
                        name: ' ',
                        clockWise: true,
                        hoverAnimation: false,
                        type: 'pie',
                        center: ['50%', '50%'],
                        radius: [innerRadius, outerRadius],
                        data: [
                            {
                                value: this.percentage,
                                name: ' ',
                                label: {
                                    normal: {
                                        position: 'center',
                                        formatter: () => displayText,
                                        textStyle: {
                                            fontSize: '21',
                                            fontFamily: config.variables.fontSecondary,
                                            fontWeight: '600',
                                            color: config.variables.fgHeading,
                                        },
                                    },
                                },
                                tooltip: {
                                    show: false,
                                },
                                itemStyle: {
                                    normal: {
                                        color: this.cardColor,
                                        shadowColor: solarTheme.shadowColor,
                                        shadowBlur: 0,
                                        shadowOffsetX: 0,
                                        shadowOffsetY: 3,
                                    },
                                },
                                hoverAnimation: false,
                            },
                            {
                                value: 100 - this.percentage,
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
                                        color: solarTheme.secondSeriesFill,
                                    },
                                },
                            },
                        ],
                    },
                ],
            };
        });
    }

    ngOnDestroy() {
        this.themeSubscription.unsubscribe();
    }
}
