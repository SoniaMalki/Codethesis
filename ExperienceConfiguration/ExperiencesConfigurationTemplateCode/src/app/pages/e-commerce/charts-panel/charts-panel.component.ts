import { Component, OnDestroy, ViewChild, AfterViewInit, Input } from '@angular/core';

import { OrdersChartComponent } from './charts/orders-chart.component';
import { ProfitChartComponent } from './charts/profit-chart.component';
import { OrderProfitChartSummary, OrdersProfitChartData } from '../../../@core/data/orders-profit-chart';
import { takeWhile } from 'rxjs/operators';

export interface OrdersChart {
  chartLabel: string[];
  linesData: number[][];
}
export interface ProfitChart {
  chartLabel: string[];
  data: number[][];
}


@Component({
  selector: 'ngx-ecommerce-charts',
  styleUrls: ['./charts-panel.component.scss'],
  templateUrl: './charts-panel.component.html',
})
export class ECommerceChartsPanelComponent implements OnDestroy {

  private alive = true;

  chartPanelSummary: OrderProfitChartSummary[];
  period: string = 'week';
  ordersChartData: OrdersChart;
  profitChartData: ProfitChart;
  
  @Input() processedData : any;
  @Input() savedData : any;

  data: any;

  @ViewChild('ordersChart', { static: true }) ordersChart: OrdersChartComponent;
  @ViewChild('profitChart', { static: true }) profitChart: ProfitChartComponent;

  constructor() {

  }

  ngAfterViewInit() {

    console.log(this.processedData)
    this.data = {
      processed: this.processedData,
      saved: this.processedData
    };

    const processedSum = this.data.processed.reduce((sum, item) => sum + Object.values(item)[0], 0);
    const savedSum = this.data.saved.reduce((sum, item) => sum + Object.values(item)[0], 0);
    const average = this.formatNumber((processedSum + savedSum) / (this.data.processed.length + this.data.saved.length));

    this.chartPanelSummary = [
      { title: 'Processed', value: processedSum },
      { title: 'Saved', value: savedSum },
      { title: 'Average', value: average },
    ];

    this.getOrdersChartData(this.period);
    this.getProfitChartData(this.period);
  }

  setPeriodAndGetChartData(value: string): void {
    if (this.period !== value) {
      this.period = value;
    }

    this.getOrdersChartData(value);
    this.getProfitChartData(value);
  }

  changeTab(selectedTab) {
    if (selectedTab.tabTitle === 'Profit') {
      this.profitChart.resizeChart();
    } else {
      this.ordersChart.resizeChart();
    }
  }

  getOrdersChartData(period: string) {
    const chartLabel = this.data.processed.map(item => Object.keys(item)[0]);
    const processedData = this.data.processed.map(item => Object.values(item)[0]);
    const savedData = this.data.saved.map(item => Object.values(item)[0]);

    this.ordersChartData = {
      chartLabel,
      linesData: [savedData, processedData],
    };
  }

  getProfitChartData(period: string) {
    const chartLabel = this.data.processed.map(item => Object.keys(item)[0]);
    const processedData = this.data.processed.map(item => Object.values(item)[0]);
    const savedData = this.data.saved.map(item => Object.values(item)[0]);

    this.profitChartData = {
      chartLabel,
      data: [savedData, processedData],
    };
  }

   formatNumber(value: number): number {
    // Format the value to one decimal place using toFixed
    const formatted = value.toFixed(2);
    // Convert the string back to a number
    return parseFloat(formatted);
  }


  ngOnDestroy() {
    this.alive = false;
  }
}
