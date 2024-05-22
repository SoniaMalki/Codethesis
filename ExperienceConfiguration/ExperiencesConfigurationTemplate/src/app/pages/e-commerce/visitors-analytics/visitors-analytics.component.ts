import { Component, OnDestroy, Input } from '@angular/core';
import { takeWhile } from 'rxjs/operators';
import { NbThemeService } from '@nebular/theme';
import { OutlineData, VisitorsAnalyticsData } from '../../../@core/data/visitors-analytics';
import { forkJoin } from 'rxjs';

@Component({
  selector: 'ngx-ecommerce-visitors-analytics',
  styleUrls: ['./visitors-analytics.component.scss'],
  templateUrl: './visitors-analytics.component.html',
})
export class ECommerceVisitorsAnalyticsComponent implements OnDestroy {
  private alive = true;


  @Input() title: string;
  
  // Input data object
  @Input() pieChartValue: any;

  chartLegend: { iconColor: string; title: string }[];
  visitorsAnalyticsData: { innerLine: number[]; outerLine: OutlineData[]; };

  constructor(private themeService: NbThemeService,
              private visitorsAnalyticsChartService: VisitorsAnalyticsData) {
    this.themeService.getJsTheme()
      .pipe(takeWhile(() => this.alive))
      .subscribe(theme => {
        this.setLegendItems(theme.variables.visitorsLegend);
      });

    forkJoin(
      this.visitorsAnalyticsChartService.getInnerLineChartData(),
      this.visitorsAnalyticsChartService.getOutlineLineChartData(),
    )
      .pipe(takeWhile(() => this.alive))
      .subscribe(([innerLine, outerLine]: [number[], OutlineData[]]) => {
        this.visitorsAnalyticsData = {
          innerLine: innerLine,
          outerLine: outerLine,
        };
      });
  }

  setLegendItems(visitorsLegend): void {
    this.chartLegend = Object.keys(this.pieChartValue).map((name, index) => ({
      iconColor: visitorsLegend[`icon${index + 1}`] || '#ccc',
      title: name,
    }));
  }

  ngOnDestroy() {
    this.alive = false;
  }
}
