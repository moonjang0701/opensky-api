#!/bin/bash
# Authenticated OpenSky Data Collection Script
# 인증된 OpenSky 데이터 수집 스크립트

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║      Y711 항로 안전성 평가 (인증된 OpenSky 계정)                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📍 실행 위치: $SCRIPT_DIR"
echo ""

# 현재 시각 확인
CURRENT_HOUR=$(date +%H)
echo "⏰ 현재 시각: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 심야 시간대 경고
if [ $CURRENT_HOUR -lt 9 ] || [ $CURRENT_HOUR -gt 18 ]; then
    echo "⚠️  경고: 현재 심야/저녁 시간대입니다 (${CURRENT_HOUR}시)"
    echo "   항공 교통량이 적어 데이터가 부족할 수 있습니다."
    echo "   권장 시간대: 오전 9시 ~ 오후 6시 (KST)"
    echo ""
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "중단되었습니다."
        exit 1
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  옵션 선택"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. 실시간 데이터 수집 (최근 1일)"
echo "2. 실시간 데이터 수집 (최근 7일)"
echo "3. 샘플 데이터로 테스트"
echo "4. 종료"
echo ""
read -p "선택 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 실시간 데이터 수집 시작 (최근 1일)..."
        echo ""
        python simple_assessment.py --airway Y711 --days 1
        ;;
    2)
        echo ""
        echo "🚀 실시간 데이터 수집 시작 (최근 7일)..."
        echo "⏱️  예상 소요 시간: 약 2-3분"
        echo ""
        python simple_assessment.py --airway Y711 --days 7
        ;;
    3)
        echo ""
        echo "🚀 샘플 데이터로 평가 시작..."
        echo ""
        python simple_assessment.py --airway Y711 --sample
        ;;
    4)
        echo ""
        echo "종료합니다."
        exit 0
        ;;
    *)
        echo ""
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  평가 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📄 보고서 파일:"
ls -t assessment_Y711_*.txt 2>/dev/null | head -1
echo ""
echo "💡 팁:"
echo "   - 낮 시간대(09:00~18:00)에 실행하면 더 많은 데이터 수집 가능"
echo "   - 보고서 파일은 현재 디렉토리에 저장됨"
echo "   - 다른 항로 평가: python simple_assessment.py --airway Y571"
echo ""
