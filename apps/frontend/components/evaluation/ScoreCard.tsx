type Props = {
    title: string;
    value: string;
    subtitle?: string;
};

export default function ScoreCard({
    title,
    value,
    subtitle,
}: Props) {

    return (

        <div className="
            rounded-xl
            border
            border-zinc-800
            bg-zinc-900
            text-cyan-200
            p-5
        ">

            <div className="text-sm text-zinc-400">
                {title}
            </div>

            <div className="mt-2 text-3xl font-bold">
                {value}
            </div>

            {subtitle && (

                <div className="mt-2 text-xs text-zinc-500">
                    {subtitle}
                </div>

            )}

        </div>

    );

}